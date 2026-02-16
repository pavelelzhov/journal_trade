import { TradeDetailsClient } from "./trade-details-client";

export default function TradeDetailsPage({ params }: { params: { id: string } }) {
  return <TradeDetailsClient id={params.id} />;
}

export function generateStaticParams() {
  return [1, 2, 3, 4, 5].map((id) => ({ id: String(id) }));
}
