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
    
    // 直接重定向到 admin，带上 token 作为 URL 参数
    return Response.redirect(`https://my-blog-7ag.pages.dev/admin/?token=${token}`, 302);
    
  } catch (error) {
    return new Response(`Error: ${error.message}`, { status: 500 });
  }
}
