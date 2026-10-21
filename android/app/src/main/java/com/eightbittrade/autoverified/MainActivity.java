package com.eightbittrade.autoverified;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.webkit.*;
import android.view.View;
import android.widget.FrameLayout;
import org.json.JSONObject;
import java.net.URL;
import java.net.HttpURLConnection;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.*;

public class MainActivity extends Activity {
 private WebView web;
 private final ExecutorService pool=Executors.newFixedThreadPool(3);
 private static final String LOCAL="https://appassets.androidplatform.net/";
 @Override public void onCreate(Bundle state){
  super.onCreate(state);
  getWindow().setStatusBarColor(Color.rgb(246,247,243));
  getWindow().setNavigationBarColor(Color.WHITE);
  getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
  FrameLayout root=new FrameLayout(this);root.setBackgroundColor(Color.rgb(246,247,243));
  root.setOnApplyWindowInsetsListener((v,insets)->{v.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());return insets.consumeSystemWindowInsets();});
  web=new WebView(this);root.addView(web,new FrameLayout.LayoutParams(-1,-1));setContentView(root);
  WebSettings settings=web.getSettings();settings.setJavaScriptEnabled(true);settings.setDomStorageEnabled(true);settings.setAllowFileAccess(false);settings.setAllowContentAccess(false);settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);settings.setSupportMultipleWindows(false);
  CookieManager.getInstance().setAcceptThirdPartyCookies(web,false);
  web.addJavascriptInterface(new InventoryBridge(),"AndroidInventory");
  web.setWebViewClient(new WebViewClient(){
   @Override public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest request){
    Uri u=request.getUrl();if("appassets.androidplatform.net".equals(u.getHost())){
     String path=u.getPath();if(path==null||path.equals("/"))path="/index.html";
     if(path.contains("..")||!path.matches("/[a-zA-Z0-9._-]+"))return new WebResourceResponse("text/plain","UTF-8",new ByteArrayInputStream(new byte[0]));
     try{String type=path.endsWith(".css")?"text/css":path.endsWith(".js")?"application/javascript":path.endsWith(".json")?"application/json":path.endsWith(".svg")?"image/svg+xml":"text/html";return new WebResourceResponse(type,"UTF-8",getAssets().open(path.substring(1)));}catch(IOException ex){return new WebResourceResponse("text/plain","UTF-8",404,"Not Found",null,new ByteArrayInputStream(new byte[0]));}
    }return null;
   }
   @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){
    String url=request.getUrl().toString();if(url.startsWith(LOCAL))return false;
    String scheme=request.getUrl().getScheme();if("https".equals(scheme)||"tel".equals(scheme)||"sms".equals(scheme)||"mailto".equals(scheme)){try{startActivity(new Intent(Intent.ACTION_VIEW,request.getUrl()));}catch(Exception ignored){}}
    return true;
   }
  });web.loadUrl(LOCAL+"index.html");
 }
 class InventoryBridge {
  @JavascriptInterface public void request(String id,String url){
   if(id==null||!id.matches("[0-9]{1,10}"))return;
   pool.execute(()->{String result=null,error=null;HttpURLConnection conn=null;
    try{
     URL target=new URL(url);
     if(!"https".equals(target.getProtocol())||!"www.carsforyouva.com".equals(target.getHost())||!target.getPath().startsWith("/inventory/")||target.getUserInfo()!=null||(target.getPort()!=-1&&target.getPort()!=443))throw new IOException("Invalid inventory address");
     conn=(HttpURLConnection)target.openConnection();conn.setInstanceFollowRedirects(false);conn.setConnectTimeout(20000);conn.setReadTimeout(25000);conn.setRequestProperty("User-Agent","AutoVerifiedInventory/1.0 (+public inventory reader)");
     if(conn.getResponseCode()!=200)throw new IOException("Dealership inventory is unavailable");
     try(InputStream input=conn.getInputStream();ByteArrayOutputStream output=new ByteArrayOutputStream()){
      byte[] buffer=new byte[16384];int read;while((read=input.read(buffer))!=-1){output.write(buffer,0,read);if(output.size()>8000000)throw new IOException("Inventory response too large");}result=new String(output.toByteArray(),StandardCharsets.UTF_8);
     }
    }catch(Exception ex){error="Unable to reach the dealership. Please try again.";}finally{if(conn!=null)conn.disconnect();}
    final String script="window.onNativeResponse("+JSONObject.quote(id)+","+(result==null?"null":JSONObject.quote(result))+","+(error==null?"null":JSONObject.quote(error))+");";
    runOnUiThread(()->{if(!isFinishing()&&web.getUrl()!=null&&web.getUrl().startsWith(LOCAL))web.evaluateJavascript(script,null);});
   });
  }
 }
 @Override public void onBackPressed(){web.evaluateJavascript("(()=>{const d=document.querySelector('dialog[open]');if(d){d.close();return true;}return false;})()",value->{if(!"true".equals(value))super.onBackPressed();});}
 @Override public void onDestroy(){web.removeJavascriptInterface("AndroidInventory");web.destroy();pool.shutdownNow();super.onDestroy();}
}
