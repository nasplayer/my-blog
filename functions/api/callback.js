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

    // 重定向回 CMS，带上 token
    const redirectUrl = new URL(stateData.redirectUri);
    redirectUrl.hash = `access_token=${tokenData.access_token}&token_type=bearer`;

    return Response.redirect(redirectUrl.toString(), 302);
  } catch (e) {
    return new Response("Error: " + e.message, { status: 500 });
  }
}
