import React from 'react';
import gql from 'graphql-tag';
import { Query } from 'react-apollo';

import { AppLink } from 'demo/approuter';


const QUERY_LIST_NOTES = gql`
    query listNotes {
        notes: listNotes {
            id
            title
            body
        }
    }
`;


export default function NotesListWrapper() {
    // ---------------------------------------------------------------
    // NOTE: Setting fetchPolicy="cache-and-network" will make sure
    // notes are reloaded every time the page is visited.
    // If we were to leave it to the default "cache-first", the list
    // would be outdated when going back from creating a new note.
    // ---------------------------------------------------------------
    return <Query query={QUERY_LIST_NOTES} fetchPolicy="cache-and-network">
        {props => <NotesList {...props} />}
    </Query>;
}


function NotesList({loading, error, data, refetch}) {
    if (loading) {
        return <div>Loading...</div>;
    }
    if (error) {
        return <div>Error: {error.message}</div>;
    }
    if (!data.notes.length) {
        return <div>There are no notes.</div>;
    }
    return <NotesListUI notes={data.notes} />;
}


function NotesListUI({notes}) {
    const itemStyle = {
        whiteSpace: 'nowrap',
        overflow: 'hidden',
    };
    return <ul>
    {notes.map(note =>
        <li key={note.id} style={itemStyle}>
            <AppLink to={`/note/${note.id}`}>
                #{note.id}: {note.title || 'Untitled'}
            </AppLink>
            {note.body ? <span style={{opacity: '.6'}}>
                {' '}&ndash; {note.body.slice(0, 200)}
            </span> : null}
        </li>
    )}
    </ul>;
}
