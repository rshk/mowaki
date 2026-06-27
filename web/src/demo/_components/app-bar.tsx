import DarkModeIcon from "@mui/icons-material/DarkMode";
import LightModeIcon from "@mui/icons-material/LightMode";
import MenuIcon from "@mui/icons-material/Menu";
import RocketLaunchIcon from "@mui/icons-material/RocketLaunch";
import AppBar from "@mui/material/AppBar";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import { useColorScheme } from "@mui/material/styles";
import Toolbar from "@mui/material/Toolbar";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import useMediaQuery from "@mui/material/useMediaQuery";
import * as React from "react";
import { NavLink } from "react-router";
import { API_URL } from "/src/lib/config";

const settings = ["Profile", "Account", "Dashboard", "Logout"];

const MENU_ITEMS: { label: string; href: string }[] = [
    { label: "Items", href: "/items" },
    { label: "Map", href: "/map" },
    { label: "Login", href: "/login" },
    { label: "Sign up", href: "/signup" },
    { label: "Logout", href: "/logout" },
    { label: "API", href: API_URL },
];

const APP_NAME = "MyApp";

function ResponsiveAppBar() {
    const [anchorElNav, setAnchorElNav] = React.useState<null | HTMLElement>(
        null,
    );

    const handleOpenNavMenu = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorElNav(event.currentTarget);
    };

    const handleCloseNavMenu = () => {
        setAnchorElNav(null);
    };

    return (
        <AppBar position="static">
            <Container maxWidth="xl">
                <Toolbar disableGutters>
                    <RocketLaunchIcon
                        sx={{ display: { xs: "none", md: "flex" }, mr: 1 }}
                    />
                    <Typography
                        variant="h6"
                        noWrap
                        component={NavLink}
                        to="/"
                        sx={{
                            mr: 2,
                            display: { xs: "none", md: "flex" },
                            fontFamily: "monospace",
                            fontWeight: 700,
                            color: "inherit",
                            textDecoration: "none",
                        }}
                    >
                        {APP_NAME}
                    </Typography>

                    <Box
                        sx={{
                            flexGrow: 1,
                            display: { xs: "flex", md: "none" },
                        }}
                    >
                        <IconButton
                            size="large"
                            aria-label="account of current user"
                            aria-controls="menu-appbar"
                            aria-haspopup="true"
                            onClick={handleOpenNavMenu}
                            color="inherit"
                        >
                            <MenuIcon />
                        </IconButton>
                        <Menu
                            id="menu-appbar"
                            anchorEl={anchorElNav}
                            anchorOrigin={{
                                vertical: "bottom",
                                horizontal: "left",
                            }}
                            keepMounted
                            transformOrigin={{
                                vertical: "top",
                                horizontal: "left",
                            }}
                            open={Boolean(anchorElNav)}
                            onClose={handleCloseNavMenu}
                            sx={{ display: { xs: "block", md: "none" } }}
                        >
                            {MENU_ITEMS.map((page, idx) => (
                                <MenuItem
                                    key={idx}
                                    onClick={handleCloseNavMenu}
                                >
                                    <Typography
                                        sx={{ textAlign: "center" }}
                                        component={NavLink}
                                        to={page.href}
                                    >
                                        {page.label}
                                    </Typography>
                                </MenuItem>
                            ))}
                        </Menu>
                    </Box>
                    <RocketLaunchIcon
                        sx={{ display: { xs: "flex", md: "none" }, mr: 1 }}
                    />
                    <Typography
                        variant="h5"
                        noWrap
                        component="a"
                        href="#app-bar-with-responsive-menu"
                        sx={{
                            mr: 2,
                            display: { xs: "flex", md: "none" },
                            flexGrow: 1,
                            fontFamily: "monospace",
                            fontWeight: 700,
                            color: "inherit",
                            textDecoration: "none",
                        }}
                    >
                        {APP_NAME}
                    </Typography>
                    <Box
                        sx={{
                            flexGrow: 1,
                            display: { xs: "none", md: "flex" },
                        }}
                    >
                        {MENU_ITEMS.map((page, idx) => (
                            <Button
                                key={idx}
                                onClick={handleCloseNavMenu}
                                sx={{ my: 2, color: "white", display: "block" }}
                                component={NavLink}
                                to={page.href}
                            >
                                {page.label}
                            </Button>
                        ))}
                    </Box>
                    <UserMenu />
                    <ColorModeToggler />
                </Toolbar>
            </Container>
        </AppBar>
    );
}
export default ResponsiveAppBar;

function UserMenu() {
    const [anchorElUser, setAnchorElUser] = React.useState<null | HTMLElement>(
        null,
    );
    const handleOpenUserMenu = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorElUser(event.currentTarget);
    };
    const handleCloseUserMenu = () => {
        setAnchorElUser(null);
    };

    return (
        <Box sx={{ flexGrow: 0 }}>
            <Tooltip title="Open settings">
                <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                    <Avatar
                        alt="Remy Sharp"
                        src="/static/images/avatar/2.jpg"
                    />
                </IconButton>
            </Tooltip>
            <Menu
                sx={{ mt: "45px" }}
                id="menu-appbar"
                anchorEl={anchorElUser}
                anchorOrigin={{
                    vertical: "top",
                    horizontal: "right",
                }}
                keepMounted
                transformOrigin={{
                    vertical: "top",
                    horizontal: "right",
                }}
                open={Boolean(anchorElUser)}
                onClose={handleCloseUserMenu}
            >
                {settings.map((setting) => (
                    <MenuItem key={setting} onClick={handleCloseUserMenu}>
                        <Typography sx={{ textAlign: "center" }}>
                            {setting}
                        </Typography>
                    </MenuItem>
                ))}
            </Menu>
        </Box>
    );
}

function ColorModeToggler() {
    const prefersDarkMode = useMediaQuery("(prefers-color-scheme: dark)");

    const { mode, setMode } = useColorScheme();
    if (!mode) {
        return null;
    }

    let currentMode: "dark" | "light" =
        mode != "system" ? mode : prefersDarkMode ? "dark" : "light";
    let nextMode: "dark" | "light" = currentMode == "light" ? "dark" : "light";

    const IconComponent: typeof LightModeIcon | typeof DarkModeIcon =
        currentMode == "dark" ? DarkModeIcon : LightModeIcon;

    const switchMode = (event: React.MouseEvent) => {
        if (event.altKey || event.ctrlKey || event.metaKey) {
            setMode("system");
        } else {
            setMode(nextMode);
        }
    };

    return (
        <Box sx={{ flexGrow: 0, mx: 1 }}>
            <Tooltip title="Hold Ctrl, Alt, ⌘, or ⎇ to reset">
                <IconButton sx={{ p: 0 }} onClick={switchMode}>
                    <IconComponent sx={{ fontSize: "1.6em" }} />
                </IconButton>
            </Tooltip>
        </Box>
    );
}
