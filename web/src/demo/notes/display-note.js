import React from 'react';
import gql from 'graphql-tag';
import { Query } from 'react-apollo';
import { Button } from 'reactstrap';

import { AppLink } from 'demo/approuter';

import DeleteNoteButton from './delete-note';


const QUERY_GET_NOTE = gql`
    query getNote($noteId: Int!) {
        note: getNote(id: $noteId) {
            id
            title
            body
        }
    }
`;


export default function DisplayNote({noteId}) {
    return <Query query={QUERY_GET_NOTE} variables={{noteId}} fetchPolicy="cache-and-network">
        {props => <NoteView noteId={noteId} {...props} />}
    </Query>;
}


function NoteView({noteId, loading, error, data}) {
    if (loading) {
        return <div>Loading note...</div>;
    }
    if (error) {
        return <div>Error: {error}</div>;
    }
    const {id, title, body} = data.note;
    return <div>
        <h1>#{id}: {title}</h1>
        <div style={{whiteSpace: 'pre-wrap'}}>
            {body}
        </div>
        <div className="mt-4">
            <DeleteNoteButton noteId={id} />{' '}
            <Button tag={AppLink} to={`/note/${noteId}/edit`}>
                Edit note
            </Button>
        </div>
    </div>;
}