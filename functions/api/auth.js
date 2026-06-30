// GitHub OAuth 配置
const CLIENT_ID = "Ov23liX7C9Unv04gVUzV";

export async function onRequestGet(context) {
  const { request } = context;
  const url = new URL(request.url);

  // 从请求中获取 redirect_uri，默认为 /admin（不带斜杠）
  let redirectUri = url.searchParams.get("redirect_uri") || `${url.origin}/admin`;
  // 确保 redirect_uri 不以 / 结尾
  if (redirectUri.endsWith('/')) {
    redirectUri = redirectUri.slice(0, -1);
  }

  // 生成 state
  const state = Math.random().toString(36).substring(2, 15);

  // 将 redirect_uri 编码到 state 中
  const stateData = JSON.stringify({ state, redirectUri });
  const encodedState = btoa(stateData);

  // 构建 GitHub OAuth URL
  const githubAuthUrl = new URL("https://github.com/login/oauth/authorize");
  githubAuthUrl.searchParams.set("client_id", CLIENT_ID);
  githubAuthUrl.searchParams.set("redirect_uri", `${url.origin}/api/callback`);
  githubAuthUrl.searchParams.set("scope", "repo");
  githubAuthUrl.searchParams.set("state", encodedState);

  return Response.redirect(githubAuthUrl.toString(), 302);
}
