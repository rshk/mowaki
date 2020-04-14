import React from 'react';
import gql from 'graphql-tag';
import { useMutation } from '@apollo/react-hooks';
import { Alert } from 'reactstrap';

import { AppRedirect } from 'demo/approuter';

import NoteForm from './note-form';


export default function CreateNotePage() {

    const [createNote, mutationStatus] = useMutation(gql`
        mutation createNote($data: CreateNoteInput!) {
            result: createNote(data: $data) {
                ok
                noteId
                errorMessage
            }
        }
    `);

    const { loading, error, data, called } = mutationStatus;

    if (error) {
        return <Alert color="danger">{error.message}</Alert>;
    }

    let errorMessage = null;

    if (called && data && data.result) {
        if (data.result.ok) {
            const { noteId } = data.result;
            return <AppRedirect to={`/note/${noteId}`} />;
        }
        errorMessage = data.result.errorMessage || 'Note creation failed';
    }

    return <NoteForm
               errorMessage={errorMessage}
               loading={loading}
               onSubmit={data=> createNote({variables: {data}})} />;

}
