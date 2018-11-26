import React from 'react';
import PropTypes from 'prop-types';
import {Redirect} from 'react-router-dom';
import gql from 'graphql-tag';
import {Query, Mutation} from 'react-apollo';

import NoteForm from './note-form';


const QUERY_GET_NOTE = gql`
    query getNote($noteId: Int!) {
        note: getNote(id: $noteId) {
            id
            title
            body
        }
    }
`;


const MUTATION_UPDATE_NOTE = gql`
    mutation updateNote($id: Int!, $title: String, $body: String) {
        updateNote(id: $id, title: $title, body: $body) {
            ok
        }
    }
`;


export default function UpdateNoteFormWrapper({noteId}) {
    // We set fetchPolicy="no-cache" as we want to make sure we have
    // fresh data for the editing form
    return <Query query={QUERY_GET_NOTE} variables={{noteId}} fetchPolicy="no-cache">
        {({data: {note}}) => {
             if (!note) {
                 return 'Loading note...';
             }
             return <UpdateNoteForm noteId={noteId} note={note} />;
        }}
    </Query>;
}


class UpdateNoteForm extends React.Component {
    static propTypes = {
        noteId: PropTypes.number.isRequired,
        note: PropTypes.shape({
            id: PropTypes.number,
            title: PropTypes.string,
            body: PropTypes.string,
        }).isRequired,
    };

    state = {
        title: this.props.note.title,
        body: this.props.note.body,
    };

    render() {
        return <Mutation mutation={MUTATION_UPDATE_NOTE}>
            {this._renderForm.bind(this)}
        </Mutation>;
    }

    _renderForm(updateNote, mutationResult) {
        const {noteId} = this.props;
        const {title, body, errorMessage} = this.state;
        const onSubmit = this._onSubmit.bind(this, updateNote);
        const onTitleChange = evt => this.setState({title: evt.target.value});
        const onBodyChange = evt => this.setState({body: evt.target.value});

        if (mutationResult.loading) {
            return <div>Saving note...</div>;
        }

        if (mutationResult.data) {
            const result = mutationResult.data.updateNote;
            if (result.ok) {
                return <Redirect to={`/note/${this.props.noteId}`} />;
            }
        }

        const formProps = {
            onSubmit,
            errorMessage,
            noteId,
            title,
            body,
            onTitleChange,
            onBodyChange,
        };

        return <NoteForm {...formProps} />;
    }

    _onSubmit(updateNote, evt) {
        evt.preventDefault();
        const {noteId: id} = this.props;
        const {title, body} = this.state;
        updateNote({variables: {id, title, body}});
    }

}
