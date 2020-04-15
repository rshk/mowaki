import React, { useState } from 'react';
import { Container, Form, FormGroup,
         Label, Input, Alert, Button} from 'reactstrap';
import gql from 'graphql-tag';
import { useQuery, useMutation } from '@apollo/react-hooks';

import Page from 'demo/page';

import { RouterApp } from 'demo/approuter';
import { doLogin, doLogout, getToken } from 'lib/auth';


export default function AuthenticationApp({prefix}) {
    const PageComponent = getToken() ? ProfilePage : LoginPage;
    return <Page appTitle="Authentication" appLink={prefix}>
        <Container className="py-3">
            <RouterApp prefix={prefix}>
                <PageComponent />
            </RouterApp>
        </Container>
    </Page>;
}


function LoginPage() {
    return <div>
        <h1>Login</h1>
        <LoginForm />
    </div>;
}


function ProfilePage() {

    const { data } = useQuery(gql`
        {
            user {
                id
                email
                displayName
                imageUrl
            }
        }
    `);

    return <div>
        <h1>User profile</h1>

        {!!(data && data.user) && <div className="d-flex flex-row mb-3">

            <div className="mr-3">
                <img src={data.user.imageUrl} alt="" style={{width: 80, height: 80}} />
            </div>

            <div>
                <div>Name: {data.user.displayName}</div>
                <div>Email: {data.user.email}</div>
                <div style={{fontSize: '.8em'}}>
                    User ID: {data.user.id}
                </div>
            </div>

        </div>}

        <Button color="danger"
                onClick={()=> doLogout({destination: '/auth'})}>
            Log out
        </Button>
    </div>;
}


function LoginForm() {

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [authenticate, { data }] = useMutation(AUTHENTICATE);

    const onSubmit = evt=> {
        evt.preventDefault();
        console.log('Login', username, password);
        authenticate({variables: {username, password}})
            .then(({data}) => {
                if (data.authenticate.ok) {
                    doLogin(data.authenticate.token, {destination: '/auth'});
                }
            });
    };

    const loginFailed = !!(
        // Received data
        data && data.authenticate &&
        // OK -> false
        !data.authenticate.ok);

    return <React.Fragment>

        {loginFailed && <Alert color="danger">
            <strong>Login failed!</strong>{' '}
            Please check your email and password.
        </Alert>}

        <Form onSubmit={onSubmit}>

            <FormGroup>
                <Label for="input-username">Email address</Label>
                <Input type="text" name="username" id="input-username"
                       value={username} onChange={e=>setUsername(e.target.value)}
                       placeholder="user@example.com" />
            </FormGroup>

            <FormGroup>
                <Label for="input-password">Password</Label>
                <Input type="password" name="password" id="input-password"
                       value={password} onChange={e=>setPassword(e.target.value)}
                       placeholder="password" />
            </FormGroup>

            <div>
                <Button block color="primary">
                    Login
                </Button>
            </div>
        </Form>

    </React.Fragment>;
}


const AUTHENTICATE = gql`
    mutation ($username: String!, $password: String!) {
        authenticate(username: $username, password: $password) {
            ok
            token
        }
    }
`;
