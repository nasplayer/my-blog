export async function onRequest(context) {
  const { env } = context;
  const clientId = "Ov23liX7C9Unv04gVUzV";
  const redirectUri = encodeURIComponent("https://my-blog-7ag.pages.dev/api/callback");
  const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=repo`;
  return Response.redirect(githubAuthUrl, 302);
}
