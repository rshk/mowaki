import React from 'react';
import gql from 'graphql-tag';
import { useQuery } from '@apollo/react-hooks';
import { Alert, Button } from 'reactstrap';

import { AppLink } from 'demo/approuter';

import DeleteNoteButton from './delete-note';

import styles from './index.scss';


export default function NoteView({noteId}) {

    const query = gql`
        query getNote($noteId: Int!) {
            note: getNote(id: $noteId) {
                id
                title
                text
            }
        }
    `;

    const options = {
        variables: { noteId },
        fetchPolicy: 'cache-and-network',
    };

    const status = useQuery(query, options);
    const { loading, error, data } = status;

    if (loading) {
        return <div>Loading note...</div>;
    }

    if (error) {
        return <Alert color="danger">{error.message}</Alert>;
    }

    const { id, title, text } = data.note;
    return <div>

        <div className={styles.userContent}>
            <h1>{title || `Note ${id}`}</h1>
            <div>
                {text}
            </div>
        </div>

        <div className="mt-4 d-flex flex-row justify-content-between">
            <Button tag={AppLink} to={`/note/${noteId}/edit`} color="secondary">
                Edit note
            </Button>
            <DeleteNoteButton noteId={id} />{' '}
        </div>

    </div>;
}
