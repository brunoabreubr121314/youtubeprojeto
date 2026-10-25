export default {
  async fetch(req, env) {
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };
    const json = (o, s = 200) =>
      new Response(JSON.stringify(o), {
        status: s,
        headers: { ...cors, "Content-Type": "application/json", "Cache-Control": "no-store" },
      });
    if (req.method === "OPTIONS") return new Response(null, { headers: cors });
    const load = async () => JSON.parse((await env.CHECKS.get("checks")) || "{}");
    if (req.method === "GET") return json(await load());
    if (req.method === "POST") {
      let b;
      try { b = await req.json(); } catch (e) { return json({ error: "json" }, 400); }
      const id = String(b.id || "");
      if (!/^[A-Za-z0-9_-]{1,40}$/.test(id)) return json({ error: "id" }, 400);
      const m = await load();
      if (b.done) m[id] = { em: new Date().toISOString() };
      else delete m[id];
      if (Object.keys(m).length > 5000) return json({ error: "limite" }, 400);
      await env.CHECKS.put("checks", JSON.stringify(m));
      return json(m);
    }
    return json({ error: "method" }, 405);
  },
};
