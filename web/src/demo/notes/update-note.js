import React from 'react';
import PropTypes from 'prop-types';
import gql from 'graphql-tag';
import { Query, Mutation } from 'react-apollo';

import { AppRedirect } from 'demo/approuter';

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
        {({data}) => {
            if (!(data && data.note)) {
                return 'Loading note...';
            }
            const {note} = data;
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
        isModified: false,
        isSuccess: false,
        errorMessage: '',
    }

    render() {
        return <Mutation mutation={MUTATION_UPDATE_NOTE}>
            {this._renderForm.bind(this)}
        </Mutation>;
    }

    _renderForm(updateNote, mutationResult) {

        const { noteId } = this.props;
        const { title, body, isModified,
                isSuccess, errorMessage } = this.state;
        const onSubmit = this._onSubmit.bind(this, updateNote);

        const onTitleChange = evt => this.setState({
            title: evt.target.value, isModified: true});

        const onBodyChange = evt => this.setState({
            body: evt.target.value, isModified: true});

        if (mutationResult.loading) {
            return <div>Saving note...</div>;
        }

        if (isSuccess) {
            return <AppRedirect to={`/note/${this.props.noteId}`} />;
        }

        // This also works, but setState in updateNote(...).then(...)
        // will throw an exception, as the component will have already
        // been unmounted by then...

        // if (mutationResult.data) {
        //     const result = mutationResult.data.updateNote;
        //     if (result.ok) {
        //         return <AppRedirect to={`/note/${this.props.noteId}`} />;
        //     }
        // }

        const formProps = {
            onSubmit,
            errorMessage,
            noteId,
            title,
            body,
            onTitleChange,
            onBodyChange,
            isModified,
            loading: mutationResult.loading,
        };

        return <NoteForm {...formProps} />;
    }

    _onSubmit(updateNote, evt) {
        evt.preventDefault();
        const {noteId: id} = this.props;
        const {title, body} = this.state;
        updateNote({variables: {id, title, body}})
            .then(({data: {updateNote: {ok, noteId, error}}}) => {
                this.setState({
                    isSuccess: ok,
                    errorMessage: ok ? '' : error,
                });
            });
    }

}
