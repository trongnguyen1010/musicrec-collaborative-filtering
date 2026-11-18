import type { Metadata } from "next";
import { Flow } from "./flow";

export const metadata: Metadata = { title: "Luồng hoạt động" };

export default function Page() {
  return <Flow />;
}
