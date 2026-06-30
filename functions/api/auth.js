// GitHub OAuth 配置
const CLIENT_ID = "Ov23liX7C9Unv04gVUzV";
const CLIENT_SECRET = "b4408da9f6f6af17b296b8705513bb1bbd9a7ab1";

// 生成随机 state
function generateState() {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

export async function onRequestGet(context) {
  const { env, request } = context;

  // 从请求中获取 redirect_uri，如果没有则使用默认值
  const url = new URL(request.url);
  const redirectUri = url.searchParams.get("redirect_uri") || `${url.origin}/admin/`;

  // 生成 state 并存储（在实际生产中应该使用 KV 存储）
  const state = generateState();

  // 构建 GitHub OAuth URL
  const githubAuthUrl = new URL("https://github.com/login/oauth/authorize");
  githubAuthUrl.searchParams.set("client_id", CLIENT_ID);
  githubAuthUrl.searchParams.set("redirect_uri", `${url.origin}/api/callback`);
  githubAuthUrl.searchParams.set("scope", "repo");
  githubAuthUrl.searchParams.set("state", state);

  // 将 redirect_uri 和 state 编码到 state 中
  const fullState = Buffer.from(JSON.stringify({ state, redirectUri })).toString('base64');
  githubAuthUrl.searchParams.set("state", fullState);

  return Response.redirect(githubAuthUrl.toString(), 302);
}
