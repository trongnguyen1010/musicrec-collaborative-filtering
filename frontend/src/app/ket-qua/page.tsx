import type { Metadata } from "next";
import { Results } from "./results";

export const metadata: Metadata = { title: "Kết quả thực nghiệm" };

export default function Page() {
  return <Results />;
}
