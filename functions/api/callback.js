export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  
  if (!code) {
    return new Response("Missing code", { status: 400 });
  }
  
  try {
    const tokenResponse = await fetch("https://github.com/login/oauth/access_token", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify({
        client_id: "Ov23liX7C9Unv04gVUzV",
        client_secret: "b4408da9f6f6af17b296b8705513bb1bbd9a7ab1",
        code: code,
      }),
    });
    
    const tokenData = await tokenResponse.json();
    
    if (tokenData.error) {
      return new Response(`Error: ${tokenData.error}`, { status: 400 });
    }
    
    const token = tokenData.access_token;
    
    const html = `<!DOCTYPE html>
<html>
<head>
  <title>认证完成</title>
  <style>
    body { font-family: sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
    .container { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 400px; margin: 0 auto; }
    .success { color: #28a745; font-size: 48px; }
    h2 { color: #333; }
    p { color: #666; }
  </style>
</head>
<body>
  <div class="container">
    <div class="success">✓</div>
    <h2>认证成功</h2>
    <p>正在跳转到后台...</p>
  </div>
  <script>
    (function() {
      var token = "${token}";
      
      // 方法1: 直接存储到 localStorage 并重定向
      try {
        var authData = {
          token: token,
          provider: 'github'
        };
        localStorage.setItem('netlify-cms-user', JSON.stringify(authData));
        localStorage.setItem('gh-oauth-token', token);
      } catch(e) {
        console.log('localStorage error:', e);
      }
      
      // 方法2: 通过 postMessage 通知 opener
      if (window.opener && window.opener !== window) {
        // 发送多种格式以确保兼容
        var messages = [
          { type: 'authorization:github:oauth-token', token: token },
          { type: 'oauth', provider: 'github', token: token },
          { kind: 'GRANT', token: token, provider: 'github' }
        ];
        
        messages.forEach(function(msg) {
          try {
            window.opener.postMessage(msg, '*');
          } catch(e) {}
        });
        
        // 延迟关闭窗口
        setTimeout(function() {
          window.close();
        }, 500);
      } else {
        // 没有 opener，直接重定向到 admin
        setTimeout(function() {
          window.location.href = '/admin/';
        }, 1000);
      }
    })();
  </script>
</body>
</html>`;
    
    return new Response(html, {
      headers: { "Content-Type": "text/html; charset=utf-8" }
    });
  } catch (error) {
    return new Response(`Error: ${error.message}`, { status: 500 });
  }
}
