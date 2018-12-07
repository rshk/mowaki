import React from 'react';
import {Redirect} from 'react-router-dom';
import gql from 'graphql-tag';
import {Mutation} from 'react-apollo';


const MUTATION_UPLOAD_NOTE = gql`
    mutation uploadNote($file: FileUpload!) {
        uploadNote(uploadedFile: $file) {
            ok
            noteId
            title
            body
        }
    }
`;


export default class UploadNoteForm extends React.Component {
    constructor(...args) {
        super(...args);
        this.state = {
            title: '',
            body: '',
            uploaddNoteId: null,
            errorMessage: '',
        };
    }

    render() {
        return <Mutation mutation={MUTATION_UPLOAD_NOTE}>
            {this._renderForm.bind(this)}
        </Mutation>;
    }

    _renderForm(uploadNote, status) {

        if (status.loading) {
            return <div>Uploading...</div>;
        }

        if (status.data) {
            const {ok, noteId, title, body} = status.data.uploadNote;

            if (ok && noteId) {
                // New note created -> head there
                return <Redirect to={`/note/${noteId}`} />;
            }

            // Mostly for debugging / testing purposes
            return (
                <div>
                    <div>Note uploaded: {noteId}</div>
                    <div><strong>Title</strong> {title}</div>
                    <div><strong>Body</strong> {body}</div>
                </div>);
        }

        const onSubmit = evt => {
            evt.preventDefault();
        };

        const onFileChange = evt => {
            const {validity: {valid}, files: [file]} = evt.target;
            if (!valid) {
                return null;
            }
            uploadNote({variables: {file}});
        };

        return <form onSubmit={onSubmit}>
            <div>
                <label htmlFor="input-text-file">Upload text file:</label>{' '}
                <input type="file" id="input-text-file" required onChange={onFileChange} />
            </div>
        </form>;
    }

}
