import Link from "next/link";

type Car = {
  id: number;
  url: string;
  year?: number;
  make?: string;
  model?: string;
  price?: number;
  price_raw?: string;
  miles?: number | null;
  thumb?: string | null;
  status?: string;
  exterior_color?: string | null;
  interior_color?: string | null;
};

function fmtPrice(n?: number) {
  if (typeof n !== "number") return "";
  return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}
function fmtMiles(n?: number | null) {
  if (n == null) return "";
  return `${n.toLocaleString()} mi`;
}

async function getCars(): Promise<Car[]> {
  const base = process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") || "http://127.0.0.1:8000";
  const res = await fetch(`${base}/scan/cars-db?limit=200`, { cache: "no-store" });
  if (!res.ok) return [];
  const data = await res.json();
  const items = Array.isArray(data) ? data : data?.items;
  return Array.isArray(items) ? items : [];
}

export default async function Page() {
  const cars = await getCars();

  return (
    <main style={{ padding: 24 }}>
      <h1 style={{ fontSize: 24, fontWeight: 600 }}>Inventory</h1>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
          gap: 16,
          marginTop: 16,
        }}
      >
        {cars.map((c) => {
          const title = [c.year, c.make, c.model].filter(Boolean).join(" ") || "Untitled";
          const price = c.price ?? undefined;
          return (
            <Link
              key={c.id}
              href={`/car?url=${encodeURIComponent(c.url)}`}
              style={{
                border: "1px solid #ddd",
                borderRadius: 12,
                padding: 16,
                textDecoration: "none",
                color: "inherit",
                display: "block",
              }}
            >
              {c.thumb && (
                <img
                  src={c.thumb}
                  alt={title}
                  style={{ width: "100%", aspectRatio: "16/9", objectFit: "cover", borderRadius: 8, marginBottom: 12 }}
                />
              )}

              <div style={{ fontSize: 18, fontWeight: 600 }}>{title}</div>
              <div style={{ opacity: 0.7, marginTop: 4, fontSize: 13 }}>
                {[c.exterior_color, c.interior_color].filter(Boolean).join(" · ")}
              </div>

              <div style={{ display: "flex", gap: 8, marginTop: 8, fontWeight: 600 }}>
                {price !== undefined && <div>{fmtPrice(price)}</div>}
                {c.miles != null && <div style={{ opacity: 0.8 }}>{fmtMiles(c.miles)}</div>}
              </div>

              {c.status && c.status !== "active" && (
                <div
                  style={{
                    marginTop: 8,
                    padding: "4px 8px",
                    background: "#f44336",
                    color: "#fff",
                    fontWeight: 600,
                    fontSize: 12,
                    borderRadius: 6,
                    display: "inline-block",
                  }}
                >
                  {c.status.toUpperCase()}
                </div>
              )}
            </Link>
          );
        })}
      </div>

      {cars.length === 0 && (
        <p style={{ marginTop: 16, opacity: 0.7 }}>No cars found. Check your API URL or try again.</p>
      )}
    </main>
  );
}
