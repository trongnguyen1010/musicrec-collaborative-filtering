import type { Metadata } from "next";
import { ExistingUser } from "./existing-user";

export const metadata: Metadata = { title: "Người dùng có sẵn" };

export default function Page() {
  return <ExistingUser />;
}
