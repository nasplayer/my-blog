// GitHub OAuth 配置
const CLIENT_ID = "Ov23liX7C9Unv04gVUzV";
const CLIENT_SECRET = "b4408da9f6f6af17b296b8705513bb1bbd9a7ab1";

export async function onRequestGet(context) {
  const { request } = context;
  const url = new URL(request.url);

  const code = url.searchParams.get("code");
  const encodedState = url.searchParams.get("state");

  if (!code || !encodedState) {
    return new Response("Missing code or state", { status: 400 });
  }

  // 解析 state
  let stateData;
  try {
    stateData = JSON.parse(atob(encodedState));
  } catch (e) {
    return new Response("Invalid state: " + e.message, { status: 400 });
  }

  // 用 code 换取 access token
  try {
    const tokenResponse = await fetch("https://github.com/login/oauth/access_token", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify({
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        code: code,
      }),
    });

    const tokenData = await tokenResponse.json();

    if (tokenData.error) {
      return new Response(`GitHub OAuth Error: ${tokenData.error_description || tokenData.error}`, { status: 400 });
    }

    if (!tokenData.access_token) {
      return new Response("No access token received", { status: 400 });
    }

    // 返回 HTML 页面，用 JavaScript 设置 token 并刷新
    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>授权成功</title>
</head>
<body>
  <p>正在登录...</p>
  <script>
    (function() {
      var token = "${tokenData.access_token}";
      // 存储 token 到 localStorage
      localStorage.setItem("decap-cms-user", JSON.stringify({
        token: token,
        backendName: "github"
      }));
      // 跳转回 admin
      window.location.href = "/admin/";
    })();
  </script>
</body>
</html>`;

    return new Response(html, {
      headers: { "Content-Type": "text/html; charset=utf-8" }
    });
  } catch (e) {
    return new Response("Error: " + e.message, { status: 500 });
  }
}
