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

    // 构建回调 URL - 确保 hash 直接跟在路径后面，没有多余的斜杠
    let redirectUri = stateData.redirectUri;
    // 移除末尾的斜杠
    if (redirectUri.endsWith('/')) {
      redirectUri = redirectUri.slice(0, -1);
    }
    
    // 直接构建完整的 URL，hash 前面不要斜杠
    const finalUrl = `${redirectUri}#access_token=${tokenData.access_token}&token_type=bearer`;

    return Response.redirect(finalUrl, 302);
  } catch (e) {
    return new Response("Error: " + e.message, { status: 500 });
  }
}
