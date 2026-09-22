import { createFileRoute } from "@tanstack/react-router";
import SignInPage from "#/components/sign-in/SignIn";

export const Route = createFileRoute("/log-in")({ component: SignInPage });
