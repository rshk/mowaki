import React from 'react';
import { BrowserRouter, Route, Switch, Redirect, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { Container, Button, Card } from 'reactstrap';

import ApolloProvider from 'lib/apollo-provider';

import ICON from './img/icon.png';
import LandingPage from './landing';
import Page from './page';
import NotesApp from './notes';
import ClockApp from './clock';
import AuthenticationApp from './authentication';


export default function DemoApp() {
    return <React.Fragment>
        <Helmet>
            <title>MoWAKi: welcome to your new app</title>
            <link rel="icon" href={ICON} />
        </Helmet>
        <ApolloProvider>
            <BrowserRouter>
                <AppRoutes />
            </BrowserRouter>
        </ApolloProvider>
    </React.Fragment>;
}


function AppRoutes() {
    return <Switch>

        <Route exact path="/" component={LandingPage} />
        <Route path="/demo" component={DemoAppsListPage} />
        <Route path="/notes" render={props => <NotesApp prefix="/notes" />} />
        <Route path="/clock" render={props => <ClockApp prefix="/clock" />} />
        <Route path="/auth" render={props => <AuthenticationApp prefix="/auth" />} />
        <Redirect to="/" />

    </Switch>;
}


function DemoAppsListPage() {
    return <Page>
        <Container>

            <Card body className="my-3">
                <h3>Notes</h3>
                <div>A simple note-taking application.</div>
                <div className="mt-3">
                    <Button tag={Link} to="/notes">
                        Go to application
                    </Button>
                </div>
            </Card>

            <Card body className="my-3">
                <h3>Authentication</h3>
                <div>Demo authentication.</div>
                <div className="mt-3">
                    <Button tag={Link} to="/auth">
                        Go to application
                    </Button>
                </div>
            </Card>

            <Card body className="my-3">
                <h3>Clock</h3>
                <div>Display server time, via websocket connection.</div>
                <div className="mt-3">
                    <Button tag={Link} to="/clock">
                        Go to application
                    </Button>
                </div>
            </Card>

        </Container>
    </Page>;
}
