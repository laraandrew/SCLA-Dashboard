// frontend/app/car/page.tsx
export const dynamic = "force-dynamic";

import Link from "next/link";
import { notFound } from "next/navigation";

// -------- helpers --------
const fmtUSD = (n: number) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(n);

function computeDisplayPrice(car: any): string {
  // Prefer already-formatted backend string, if present & non-empty
  const raw = (car?.price_raw ?? "").toString().trim();
  if (raw) return raw;

  // Fall back to numeric `price` (can be string or number or null)
  const numeric = Number(car?.price);
  if (Number.isFinite(numeric) && numeric > 0) return fmtUSD(numeric);

  return "Price on request";
}

async function getCar(url: string) {
  const base = process.env.NEXT_PUBLIC_API_URL!;
  const r = await fetch(`${base}/scan/detail?url=${encodeURIComponent(url)}`, {
    cache: "no-store",
  });
  if (!r.ok) return null;
  return r.json();
}

export default async function CarPage({
  searchParams,
}: {
  searchParams?: { url?: string };
}) {
  const url = searchParams?.url;
  if (!url) return notFound();

  const car = await getCar(url);
  if (!car) return notFound();

  const price = computeDisplayPrice(car);
  const base = process.env.NEXT_PUBLIC_API_URL!;
  // Backend you’ll wire up: return a PNG (or PDF) file for the given URL
  const stickerHref = `${process.env.NEXT_PUBLIC_API_URL}/stickers/generate?url=${encodeURIComponent(car.url)}`
;

  return (
    <main style={{ padding: 24, maxWidth: 1100, margin: "0 auto" }}>
      <Link href="/" style={{ textDecoration: "none", color: "#6b46c1", fontWeight: 600 }}>← Back</Link>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 24,
          marginTop: 16,
        }}
      >
        <img
          src={car.thumb || "/placeholder.png"}
          alt={`${car.year ?? ""} ${car.make ?? ""} ${car.model ?? ""}`.trim()}
          style={{ width: "100%", height: 480, objectFit: "cover", borderRadius: 12 }}
        />

        <div>
          <h1 style={{ margin: "0 0 8px", fontSize: 42, lineHeight: 1.1 }}>
            {car.year} {car.make} {car.model}
          </h1>

          <div style={{ opacity: 0.7, marginBottom: 12, fontSize: 18 }}>
            {car.exterior_color || "—"} • {car.interior_color || "—"}
          </div>

          <div style={{ fontSize: 28, fontWeight: 800, marginBottom: 16 }}>
            {price}
          </div>

          <ul style={{ lineHeight: 1.9, paddingLeft: 18, marginBottom: 20 }}>
            <li>Miles: {car.miles?.toLocaleString?.() ?? car.miles ?? "—"}</li>
            <li>Body: {car.body_style || "—"}</li>
            <li>Transmission: {car.transmission || "—"}</li>
            <li>Engine: {car.engine || "—"}</li>
            <li>VIN: {car.vin || "—"}</li>
            <li>Stock: {car.stock || "—"}</li>
          </ul>

          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <a
              href={car.url}
              target="_blank"
              rel="noreferrer"
              style={{
                padding: "10px 14px",
                borderRadius: 10,
                border: "1px solid #DDD",
                textDecoration: "none",
                fontWeight: 600,
              }}
            >
              View on SportscarLA ↗
            </a>

            {/* Sticker button (opens file in new tab; backend should return image/pdf) */}
            <a
              href={stickerHref}
              target="_blank"
              rel="noreferrer"
              style={{
                padding: "10px 14px",
                borderRadius: 10,
                background: "#111827",
                color: "white",
                textDecoration: "none",
                fontWeight: 700,
              }}
            >
              Generate sticker
            </a>
          </div>
        </div>
      </div>
    </main>
  );
}
