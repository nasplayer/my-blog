export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  
  if (!code) {
    return new Response("Missing code", { status: 400 });
  }
  
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
  
  const html = `
<!DOCTYPE html>
<html>
<head><title>认证完成</title></head>
<body>
<script>
if (window.opener) {
  window.opener.postMessage(
    { type: 'authorization:github:oauth-token', token: '${tokenData.access_token}' },
    'https://my-blog-7ag.pages.dev'
  );
  window.close();
} else {
  document.body.innerHTML = '<h2>认证成功！</h2><p>请关闭此窗口并刷新页面。</p>';
}
</script>
</body>
</html>`;
  
  return new Response(html, {
    headers: { "Content-Type": "text/html" }
  });
}
