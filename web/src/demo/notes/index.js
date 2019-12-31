import React from 'react';
import { Route, Switch } from 'react-router-dom';
import { Container, Button } from 'reactstrap';

import Page from 'demo/page';

import NotesList from './notes-list';
import DisplayNote from './display-note';
import CreateNoteForm from './create-note';
import UpdateNoteForm from './update-note';
import UploadNoteForm from './upload-note';

import { RouterApp, AppLink } from 'demo/approuter';


export default function NotesApp({prefix}) {
    return <Page appTitle="Notes" appLink={prefix}>
        <Container className="py-3">
            <RouterApp prefix={prefix}>
                <Switch>
                    {/* AppRoute breaks Switch */}
                    <Route exact path={`${prefix}`} component={NotesListPage} />
                    <Route exact path={`${prefix}/new`} component={NoteCreatePage} />
                    <Route exact path={`${prefix}/upload`} component={NoteUploadPage} />
                    <Route exact path={`${prefix}/note/:noteId`}
                           render={({match: {params: {noteId}}}) =>
                               <NoteDisplayPage noteId={parseInt(noteId, 10)} /> } />
                    <Route exact path={`${prefix}/note/:noteId/edit`}
                           render={({match: {params: {noteId}}}) =>
                               <NoteUpdatePage noteId={parseInt(noteId, 10)} /> } />
                </Switch>
            </RouterApp>
        </Container>
    </Page>
    ;
}


function NotesListPage() {
    return <div>
        <h1>List notes</h1>
        <div>
            <Button tag={AppLink} to="/new" color="success">
                Create new note
            </Button>
            <Button tag={AppLink} to="/upload" color="secondary" className="ml-3">
                Upload from file
            </Button>
        </div>
        <div style={{marginTop: '20px'}}>
            <NotesList />
        </div>
    </div>;
}


function SubPage({children, backLink="/", backText="Back to list"}) {
    return <div>
        <div>
            <AppLink to={backLink}>{backText}</AppLink>
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
