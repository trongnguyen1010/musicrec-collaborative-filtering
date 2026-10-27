import type { Metadata } from "next";
import { NewUser } from "./new-user";

export const metadata: Metadata = { title: "Người dùng mới" };

export default function Page() {
  return <NewUser />;
}
