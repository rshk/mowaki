import { createFileRoute } from "@tanstack/react-router";
//import MarketingPage from "../components/marketing-page/MarketingPage.tsx";
import MarketingPage from "#/components/marketing-page/MarketingPage";

export const Route = createFileRoute("/")({ component: App });

function App() {
    return <main>Hello</main>;
}
