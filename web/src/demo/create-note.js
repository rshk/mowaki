import React from 'react';
import {Redirect} from 'react-router-dom';
import gql from 'graphql-tag';
import {Mutation} from 'react-apollo';

import NoteForm from './note-form';


const MUTATION_CREATE_NOTE = gql`
    mutation createNote($title: String!, $body: String) {
        createNote(title: $title, body: $body) {
            ok
            noteId
        }
    }
`;


export default class CreateNoteForm extends React.Component {
    constructor(...args) {
        super(...args);
        this.state = {
            title: '',
            body: '',
            createdNoteId: null,
            errorMessage: '',
        };
    }

    render() {
        return <Mutation mutation={MUTATION_CREATE_NOTE}>
            {this._renderForm.bind(this)}
        </Mutation>;
    }

    _renderForm(createNote, {loading, error}) {

        const {title, body, errorMessage, createdNoteId} = this.state;
        const onSubmit = this._onSubmit.bind(this, createNote);
        const onTitleChange = evt => this.setState({title: evt.target.value});
        const onBodyChange = evt => this.setState({body: evt.target.value});

        if (createdNoteId) {
            return <Redirect to={`/note/${createdNoteId}`} />;
        }

        const formProps = {
            onSubmit,
            errorMessage,
            noteId: null,
            title,
            body,
            onTitleChange,
            onBodyChange,
            loading,
            error,
        };

        return <NoteForm {...formProps} />;
    }

    _onSubmit(createNote, evt) {
        evt.preventDefault();
        const {title, body} = this.state;
        createNote({variables: {title, body}})
            .then(({data: {createNote: {ok, noteId, error}}}) => {
                if (ok) {
                    this.setState({createdNoteId: noteId});
                }
                else {
                    this.setState({errorMessage: error});
                }
            });
    }

}
