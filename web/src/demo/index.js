import React from 'react';
import { BrowserRouter, Route, Switch, Redirect, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { Container, Button } from 'reactstrap';

import {API_URL} from '../lib/apollo';
import ApolloProvider from '../lib/apollo-provider';

import styles from './index.scss';

import NotesList from './notes-list';
import DisplayNote from './display-note';
import CreateNoteForm from './create-note';
import UpdateNoteForm from './update-note';
import UploadNoteForm from './upload-note';
import CurrentTime from './current-time';
import ErrorBoundary from './error-boundary';

import ICON from './img/icon.png';
import LOGO from './img/mowaki.png';


export default function DemoApp() {
    return <React.Fragment>
        <Helmet>
            <title>MoWAKi demo app</title>
            <link rel="icon" href={ICON} />
        </Helmet>
        <ApolloProvider>
            <BrowserRouter>
                <div>
                    <MowakiIntro />
                    <Container>
                        <div className="text-right">
                            <Button tag="a" href={API_URL} color="primary" outline>
                                Access GraphiQL
                            </Button>
                        </div>
                        <ErrorBoundary>
                            <AppRoutes />
                        </ErrorBoundary>
                    </Container>
                </div>
            </BrowserRouter>
        </ApolloProvider>
    </React.Fragment>;
}


function AppRoutes() {
    return <Switch>
        <Route exact path="/" component={NotesListPage} />
        <Route exact path="/new" component={NoteCreatePage} />
        <Route exact path="/upload" component={NoteUploadPage} />
        <Route exact path="/note/:noteId"
               render={({match: {params: {noteId}}}) =>
                   <NoteDisplayPage noteId={parseInt(noteId, 10)} /> } />
        <Route exact path="/note/:noteId/edit"
               render={({match: {params: {noteId}}}) =>
                   <NoteUpdatePage noteId={parseInt(noteId, 10)} /> } />
        <Redirect to="/" />
    </Switch>;
}


function MowakiIntro() {
    return <div className={styles.header}>
        <Container>
            <div>
                <img src={LOGO} alt="" className={styles.logo} />
            </div>
            <h1 className={styles.siteTitle}>
                Welcome to MoWAKi
            </h1>
            <div>
                Your new project has been set up correctly.<br/>
                Feel free to play around with the demo app.
            </div>
        </Container>
    </div>;
}


function NotesListPage() {
    return <div>
        <h1>List notes</h1>
        <div>
            <Button tag={Link} to="/new" color="success">
                Create new note
            </Button>
            <Button tag={Link} to="/upload" color="secondary" className="ml-3">
                Upload from file
            </Button>
        </div>
        <div style={{marginTop: '20px'}}>
            <NotesList />
        </div>
        <div>
            <hr/>
            <div style={{textAlign: 'center'}}>
                <div style={{opacity: '.7'}}>
                    Current UTC time, via GraphQL subscription:
                </div>
                <div style={{fontSize: '2em'}}>
                    <CurrentTime />
                </div>
            </div>
        </div>
    </div>;
}


function SubPage({children, backLink="/", backText="Back to list"}) {
    return <div>
        <div>
            <Link to={backLink}>{backText}</Link>
        </div>
        {children}
    </div>;
}


function NoteCreatePage() {
    return <SubPage>
        <h1>Create note</h1>
        <CreateNoteForm />
    </SubPage>;
}


function NoteUploadPage() {
    return <SubPage>
        <h1>Upload note</h1>
        <UploadNoteForm />
    </SubPage>;
}


function NoteUpdatePage({noteId}) {
    return <SubPage backLink={`/note/${noteId}`} backText="Back to note">
        <h1>Edit note</h1>
        <UpdateNoteForm {...{noteId}} />
    </SubPage>;
}


function NoteDisplayPage({noteId}) {
    return <SubPage>
        <DisplayNote noteId={noteId} />
    </SubPage>;
}
