import React from 'react';
import gql from 'graphql-tag';
import { Mutation } from 'react-apollo';

import { AppRedirect } from 'demo/approuter';

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

    state = {
        title: '',
        body: '',
        isModified: false,
        isSuccess: false,
        createdNoteId: null,
        errorMessage: '',
    }

    render() {
        return <Mutation mutation={MUTATION_CREATE_NOTE}>
            {this._renderForm.bind(this)}
        </Mutation>;
    }

    _renderForm(createNote, mutationResult) {

        const { title, body, isModified,
                isSuccess, createdNoteId, errorMessage } = this.state;
        const onSubmit = this._onSubmit.bind(this, createNote);

        const onTitleChange = evt => this.setState({
            title: evt.target.value, isModified: true});

        const onBodyChange = evt => this.setState({
            body: evt.target.value, isModified: true});

        if (mutationResult.loading) {
            return <div>Creating note...</div>;
        }

        if (isSuccess) {
            return <AppRedirect to={`/note/${createdNoteId}`} />;
        }

        // This also works, but setState in createNote(...).then(...)
        // will throw an exception, as the component will have already
        // been unmounted by then...

        // if (mutationResult.data) {
        //     const result = mutationResult.data.createNote;
        //     if (result.ok) {
        //         return <AppRedirect to={`/note/${result.noteId}`} />;
        //     }
        // }

        const formProps = {
            onSubmit,
            errorMessage,
            noteId: null,
            title,
            body,
            onTitleChange,
            onBodyChange,
            isModified,
            loading: mutationResult.loading,
        };

        return <NoteForm {...formProps} />;
    }

    _onSubmit(createNote, evt) {
        evt.preventDefault();
        const {title, body} = this.state;
        createNote({variables: {title, body}})
            .then(({data: {createNote: {ok, noteId, error}}}) => {
                this.setState({
                    isSuccess: ok,
                    errorMessage: ok ? '' : error,
                    createdNoteId: ok ? noteId : null,
                });
            });
    }

}
