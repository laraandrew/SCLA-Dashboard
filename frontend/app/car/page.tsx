import { notFound } from "next/navigation";

async function getCar(url: string) {
  const r = await fetch(
    process.env.NEXT_PUBLIC_API_URL + "/scan/car?url=" + encodeURIComponent(url),
    { cache: "no-store" }
  );
  if (!r.ok) return null;
  return r.json();
}

export default async function CarPage({ searchParams }: { searchParams?: { url?: string } }) {
  const url = searchParams?.url;
  if (!url) return notFound();

  const car = await getCar(url);
  if (!car) return notFound();

  return (
    <main style={{ padding: 24 }}>
      <h1 style={{ fontSize: 24, fontWeight: 600 }}>{car.title}</h1>

      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          gap: 16,
          marginTop: 16,
        }}
      >
        <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 16 }}>
          <h2 style={{ fontWeight: 600 }}>Details</h2>
          <div>Miles: {car.mileage}</div>
          <div>Price: {car.price}</div>
          {car.sold && (
            <div
              style={{
                marginTop: 8,
                padding: "4px 8px",
                background: "#f44336",
                color: "white",
                fontWeight: 600,
                fontSize: 12,
                borderRadius: 6,
                display: "inline-block",
              }}
            >
              SOLD
            </div>
          )}
        </div>

        <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 16 }}>
          <h2 style={{ fontWeight: 600 }}>Source</h2>
          <a href={car.url} target="_blank" rel="noopener noreferrer">
            View on SportscarLA
          </a>
        </div>
      </section>
    </main>
  );
}
