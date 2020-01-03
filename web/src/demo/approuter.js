import React from 'react';
import { Route, Link, NavLink, Redirect } from 'react-router-dom';


const AppPrefixContext = React.createContext(null);
AppPrefixContext.displayName = 'AppPrefixContext';


export function RouterApp({prefix, children}) {
    return <AppPrefixContext.Provider value={prefix}>
        {children}
    </AppPrefixContext.Provider>;
}


export const AppRoute = makeWrappedComponent(
    Route, (prefix, {path, ...props}) => ({
        path: resolvePath(prefix, path),
        ...props,
}));


export const AppLink = makeWrappedComponent(
    Link, (prefix, {to, ...props}) => ({
        to: resolveTo(prefix, to),
        ...props,
}));


export const AppNavLink = makeWrappedComponent(
    NavLink, (prefix, {to, ...props}) => ({
        to: resolveTo(prefix, to),
        ...props,
}));


export const AppRedirect = makeWrappedComponent(
    Redirect, (prefix, {to, from, ...props}) => ({
        to: resolveTo(prefix, to),
        from: resolvePath(prefix, from),
        ...props,
}));


function makeWrappedComponent(BaseComponent, makeProps) {
    return props => <AppPrefixContext.Consumer>
        {prefix => <BaseComponent {...makeProps(prefix, props)} />}
    </AppPrefixContext.Consumer>;
}


function resolvePath(prefix, path) {
    if (!prefix) {
        return path;
    }
    if (typeof path === 'undefined') {
        return undefined;
    }
    if (path == null) {
        return null;
    }
    if (Array.isArray(path)) {
        return path.map(item => prefix + item);
    }
    return prefix + path;
}


function resolveTo(prefix, to) {
    const obType = typeof to;

    if (obType === 'string') {
        return resolvePath(prefix, to);
    }
    if (obType === 'object') {
        return {
            pathname: resolvePath(prefix, to.pathname),
            ...to,
        };
    }
    if (obType === 'function') {
        return (...args) => resolvePath(prefix, to(...args));
    }
    return to;
}
