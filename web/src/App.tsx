import * as React from "react";
import {
    BrowserRouter,
    Routes,
    Route,
    Outlet,
    useParams,
} from "react-router";
import ResponsiveAppBar from "./demo/_components/app-bar";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import Container from "@mui/material/Container";
import apiClient from "/src/lib/api-client";
import { Button } from "@mui/material";

const theme = createTheme({
    colorSchemes: {
        dark: true,
    },
});

function App() {
    return (
        <ThemeProvider theme={theme}>
            <BrowserRouter>
                <AppRoutes />
            </BrowserRouter>
        </ThemeProvider>
    );
}

function AppRoutes() {
    return (
        <Routes>
            <Route element={<MainLayout />}>
                <Route index element={<Homepage />} />
                <Route path="items" element={<ItemsIndex />} />
                <Route path="item/:id" element={<ItemDisplay />} />
            </Route>

            <Route element={<LoginLayout />}>
                <Route path="login" element={<Login />} />
                <Route path="signup" element={<Signup />} />
                <Route path="logout" element={<Logout />} />
            </Route>

            <Route element={<WideLayout />}>
                <Route path="map" element={<Map />} />
            </Route>
        </Routes>
    );
}

export default App;

// Demo components

function MainLayout() {
    return (
        <Container maxWidth="lg">
            <div>
                <Navigation />
            </div>
            <Outlet />
        </Container>
    );
}

function LoginLayout() {
    return (
        <div>
            <Navigation />
            <div
                style={{
                    maxWidth: "600px",
                    margin: "100px auto",
                    border: "solid 1px #008",
                }}
            >
                <div>
                    <div>SomeApp - Login layout</div>
                </div>
                <Outlet />
            </div>
        </div>
    );
}

function WideLayout() {
    return (
        <div>
            <div>
                <div>SomeApp - Wide layout</div>
                <Navigation />
            </div>
            <Outlet />
        </div>
    );
}

function Navigation() {
    return <ResponsiveAppBar />;
}

function Homepage() {
    return (
        <div>
            <h1>Dashboard</h1>
            <DemoRequests />
        </div>
    );
}

function ItemsIndex() {
    return (
        <div>
            <h1>Items</h1>
        </div>
    );
}

function ItemDisplay() {
    const { id } = useParams();
    return (
        <div>
            <h1>Item {id}</h1>
        </div>
    );
}

function Login() {
    return <div>login form</div>;
}

function Signup() {
    return <div>sign up</div>;
}

function Logout() {
    return <div>log out</div>;
}

function Map() {
    return <div>Wide map</div>;
}

function DemoRequests() {
    type ReqState = {
        data?: object;
        error?: object;
    };

    const [state, setState] = React.useState<ReqState>({});
    const doRequest = () => {
        apiClient._client
            .get("/_dev")
            .then((data) => setState({ data }))
            .catch((error) => setState({ error }));
    };

    /* React.useEffect(() => doRequest(), []); */

    const doLogout = () => {
        apiClient._client
            .post("/_dev/logout", {})
            .then((data) => setState({ data }))
            .catch((error) => setState({ error }));
    };

    const doGet403 = () => {
        apiClient._client
            .post("/_dev/403", {})
            .then((data) => setState({ data }))
            .catch((error) => setState({ error }));
    };

    const doGet403Upgrade = () => {
        apiClient._client
            .post("/_dev/403-upgrade", {})
            .then((data) => setState({ data }))
            .catch((error) => setState({ error }));
    };

    return (
        <div>
            {!!state.data && <pre>{JSON.stringify(state.data, null, 4)}</pre>}
            {!!state.error && <pre>{"=== ERROR ===\n"}{JSON.stringify(state.error, null, 4)}</pre>}
            <div>
                <Button variant="contained" onClick={doRequest}>
                    Refresh
                </Button>
                <Button variant="contained" onClick={doLogout}>
                    New session
                </Button>
                <Button variant="contained" onClick={doGet403}>
                    Permanent 403
                </Button>
                <Button variant="contained" onClick={doGet403Upgrade}>
                    403 with upgrade
                </Button>
            </div>
        </div>
    );
}
