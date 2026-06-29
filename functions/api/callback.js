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
    body { font-family: sans-serif; text-align: center; padding: 50px; }
    .success { color: green; }
  </style>
</head>
<body>
  <h2 class="success">✓ 认证成功</h2>
  <p>正在返回后台...</p>
  <script>
    (function() {
      var token = "${token}";
      // Decap CMS 期望的消息格式
      if (window.opener && window.opener !== window) {
        window.opener.postMessage(
          { 
            type: 'authorization:github:oauth-token',
            token: token,
            provider: 'github'
          },
          '*'
        );
        setTimeout(function() { window.close(); }, 100);
      } else {
        // 如果没有 opener，存储 token 并重定向
        localStorage.setItem('netlify-cms-user', JSON.stringify({token: token}));
        window.location.href = '/admin/';
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
