export async function onRequest(context) {
  const clientId = "Ov23liX7C9Unv04gVUzV";
  const redirectUri = encodeURIComponent("https://my-blog-7ag.pages.dev/api/callback");
  const scope = encodeURIComponent("repo,user");
  const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}`;
  return Response.redirect(githubAuthUrl, 302);
}
