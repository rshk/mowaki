import * as React from "react";
import { BrowserRouter, Routes, Route, Outlet, useParams } from "react-router";
import ResponsiveAppBar from "./demo/_components/app-bar";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import Container from "@mui/material/Container";
import apiClient from "/src/lib/api-client";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import CssBaseline from "@mui/material/CssBaseline";
import {
    useQuery,
    useMutation,
    useQueryClient,
    QueryClientProvider,
} from "@tanstack/react-query";
import { AuthorizationError } from "./lib/api-client/rest-client";
import queryClient from "./lib/query-client";

const theme = createTheme({
    colorSchemes: {
        dark: true,
    },
});

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <BrowserRouter>
                    <AppRoutes />
                </BrowserRouter>
            </ThemeProvider>
        </QueryClientProvider>
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
            <h1>Login with webauthn</h1>
            <WebauthnLoginForm />
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
    const queryClient = useQueryClient();

    const query = useQuery({
        queryKey: ["_dev"],
        queryFn: () => apiClient._client.get("/_dev"),
    });

    const logoutMutation = useMutation({
        mutationFn: () => apiClient._client.post("/_dev/logout", {}),
        onSuccess: async () => {
            await queryClient.invalidateQueries({
                queryKey: ["_dev"],
            });
        },
    });

    const rotateMutation = useMutation({
        mutationFn: () => apiClient._client.post("/_dev/rotate", {}),
        onSuccess: async () => {
            await queryClient.invalidateQueries({
                queryKey: ["_dev"],
            });
        },
    });

    const get403Mutation = useMutation({
        mutationFn: () => apiClient._client.post("/_dev/403", {}),
    });
    const get403upMutation = useMutation({
        mutationFn: () => apiClient._client.post("/_dev/403-upgrade", {}),
    });

    const doRequest = () => {
        query.refetch();
    };

    const doLogout = () => {
        logoutMutation.mutate();
    };

    const doGet403 = () => {
        get403Mutation.mutate();
    };

    const doGet403Upgrade = () => {
        get403upMutation.mutate();
    };

    if (get403Mutation.error) {
        console.log("ERROR", get403Mutation.error);
    }

    return (
        <div>
            {!!query.data && <pre>{JSON.stringify(query.data, null, 4)}</pre>}
            {get403Mutation.error instanceof AuthorizationError && (
                <pre>
                    {"=== ERROR ===\n"}
                    {JSON.stringify(get403Mutation.error, null, 4)}
                </pre>
            )}
            {!!get403upMutation.error && (
                <pre>
                    {"=== ERROR ===\n"}
                    {JSON.stringify(get403upMutation.error, null, 4)}
                </pre>
            )}
            <div>
                <Button variant="contained" onClick={doRequest}>
                    Refresh
                </Button>
                <Button variant="contained" onClick={doLogout}>
                    New session
                </Button>
                <Button
                    variant="contained"
                    onClick={() => {
                        rotateMutation.mutate();
                    }}
                >
                    Rotate secret
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

function WebauthnLoginForm() {
    const [formState, setFormState] = React.useState({});
    const onSubmit = () => {};

    return (
        <div>
            <form onSubmit={onSubmit}>
                <Box>
                    <TextField
                        id="email-addr"
                        label="Email address"
                        variant="outlined"
                        fullWidth
                        autoComplete="username webauthn"
                        type="email"
                    />
                </Box>
            </form>
        </div>
    );
}
