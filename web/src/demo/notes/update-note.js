import React from 'react';
import PropTypes from 'prop-types';
import gql from 'graphql-tag';
import { useQuery, useMutation } from '@apollo/react-hooks';
import { Alert } from 'reactstrap';

import { AppRedirect } from 'demo/approuter';

import NoteForm from './note-form';


export default function UpdateNotePage({ noteId }) {
    // We set fetchPolicy="no-cache" as we want to make sure we have
    // fresh data for the editing form

    const queryStatus = useQuery(gql`
        query getNote($noteId: Int!) {
            note: getNote(id: $noteId) {
                id
                title
                text
            }
        }
    `, {
        variables: { noteId },
        fetchPolicy: "no-cache",
    });

    const { loading, error, data } = queryStatus;

    if (loading) {
        return <div>Loading notes...</div>;
    }

    if (error) {
        return <Alert color="danger">{error.message}</Alert>;
    }

    if (data && !data.note) {
        return <div>Not found</div>;
    }

    return <UpdateNoteForm noteId={noteId} note={data.note} />;
}


function UpdateNoteForm({ noteId, note }) {

    const [updateNote, mutationStatus] = useMutation(gql`
        mutation updateNote($id: Int!, $data: UpdateNoteInput!) {
            updateNote(id: $id, data: $data) {
                ok
                note {
                    id
                    title
                    text
                }
            }
        }
    `);

    const { loading, error, data, called } = mutationStatus;

    if (loading) {
        return <div>Saving note...</div>;
    }

    if (error) {
        return <Alert color="danger">{error.message}</Alert>;
    }

    if (called && data && data.updateNote.ok) {
        return <AppRedirect to={`/note/${noteId}`} />;
    }

    const errorMessage =
        (called && data && !data.updateNote.ok) ?
        'Error updating note' : null;

    const onSubmit = (data)=> {
        updateNote({variables: {id: noteId, data}});
    };

    const formData = {
        title: note.title,
        text: note.text,
    };

    return <NoteForm
               formData={formData}
               errorMessage={errorMessage}
               loading={loading}
               onSubmit={onSubmit}
               noteId={noteId} />;
}


UpdateNoteForm.propTypes = {
    noteId: PropTypes.number.isRequired,
    note: PropTypes.shape({
        id: PropTypes.number.isRequired,
        title: PropTypes.string,
        text: PropTypes.string,
    }).isRequired,
};
