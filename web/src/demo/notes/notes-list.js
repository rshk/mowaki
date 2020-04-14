import React from 'react';
import gql from 'graphql-tag';
import { useQuery } from '@apollo/react-hooks';
import { Alert, ListGroup, ListGroupItem } from 'reactstrap';

import { AppLink } from 'demo/approuter';

import styles from './index.scss';


export default function NotesList() {

    const query = gql`
        query listNotes {
            notes: listNotes {
                id
                title
                summary(length: 300)
            }
        }
    `;

    const { loading, error, data } =
        useQuery(query, {fetchPolicy: 'cache-and-network'});

    if (loading) {
        return <div>Loading notes...</div>;
    }

    if (error) {
        return <Alert color="danger">
            {error.message}
        </Alert>;
    }

    if (!data.notes.length) {
        return <div className="text-muted">
            There are no notes.
        </div>;
    }

    return <NotesListUI notes={data.notes} />;
}


function NotesListUI({notes}) {
    return <ListGroup>
        {notes.map(note =>
            <ListGroupItem key={note.id} tag={AppLink} to={`/note/${note.id}`}>

                <div className={styles.noteListItem}>
                    <span className={styles.noteListTitle}>
                        {note.title || `Note ${note.id}`}{' '}
                    </span>

                    <span className={styles.noteListText}>
                        {note.summary}
                    </span>
                </div>

            </ListGroupItem>
        )}
    </ListGroup>;
}
