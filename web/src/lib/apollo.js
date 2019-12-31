import {ApolloClient} from 'apollo-client';
import {InMemoryCache} from 'apollo-cache-inmemory';
import {onError} from 'apollo-link-error';
import {ApolloLink} from 'apollo-link';
import {createUploadLink} from 'apollo-upload-client';
import {createHttpLink} from 'apollo-link-http';
import {setContext} from 'apollo-link-context';
import {split} from 'apollo-link';
import {WebSocketLink} from 'apollo-link-ws';
import {getMainDefinition} from 'apollo-utilities';

import {doLogout, getToken} from './auth';

function replaceLocalhost(url) {
    // If API_URL is simply http://localhost/... -> replace with current domain
    // This allows development installations to be accessed from multiple locations
    // TODO: should we use some other domain instead of localhost?
    const {protocol, hostname} = document.location;
    return url.replace('http://localhost', `${protocol}//${hostname}`);
}


export const API_URL = replaceLocalhost(
    process.env.API_URL || 'http://localhost:5000/graphql');


const WEBSOCKET_URL = (
    API_URL
        .replace(/^http(s?):\/\/(.*)/, 'ws$1://$2')
        .replace(/\/graphql$/, '/subscriptions')  // HACK
);

const ENABLE_UPLOADS = true;


const onErrorLink = onError(({graphQLErrors, networkError}) => {

    if (graphQLErrors) {
        graphQLErrors.map(({message, locations, path, extensions})=> {

            console.log(
                `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`);

            // 401 exception caught by GraphQL will add a
            // "login_required" extension.
            if (extensions && extensions.login_required) {
                doLogout();
            }

            return null;
        });
    }

    if (networkError) {
        console.log(`[Network error]: ${networkError}`);

        if (networkError.statusCode === 401) {
            doLogout();  // Force re-login
        }
    }
});


const httpLink = (() => {
    const config = {
        uri: API_URL,
        credentials: 'same-origin'
    };

    if (ENABLE_UPLOADS) {
        return createUploadLink(config);
    }
    return createHttpLink(config);
})();


const authLink = setContext((_, {headers: extraHeaders}) => {
    const token = getToken();
    const headers = {...extraHeaders};
    if (token) {
        headers.authorization = `Bearer ${token}`;
    }
    return {headers};
});


const wsLink = new WebSocketLink({
    uri: WEBSOCKET_URL,
    options: {
        reconnect: true,
        connectionParams: {
            authToken: getToken(),
        },
    }
});


// using the ability to split links, you can send data to each link
// depending on what kind of operation is being sent
const link = split(
    // split based on operation type
    ({ query }) => {
        const {kind, operation} = getMainDefinition(query);
        // console.log('SPLIT LINK', kind, operation);
        return kind === 'OperationDefinition' && operation === 'subscription';
    },
    wsLink,
    ApolloLink.from([
        onErrorLink,
        authLink,
        httpLink,
    ]),
);


const cache = new InMemoryCache();


const LOCALSTORAGE_AUTH_TOKEN_KEY = 'auth-token';

const resolvers = {

    Query: {
        authToken() {
            return localStorage.getItem(LOCALSTORAGE_AUTH_TOKEN_KEY);
        },
    },

    Mutation: {
        setAuthToken(_, {token}, {cache}) {
            localStorage.setItem(LOCALSTORAGE_AUTH_TOKEN_KEY, token);

            const data = {
                __typename: 'Query',
                authToken: token,
            };

            cache.writeData({data});

            return data;
        },
    },

};

const client = new ApolloClient({link, cache, resolvers});

export default client;
