import React from 'react';
import gql from 'graphql-tag';
import { Mutation } from 'react-apollo';
import { Form, FormGroup, CustomInput } from 'reactstrap';

import { AppRedirect } from 'demo/approuter';


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
                return <AppRedirect to={`/note/${noteId}`} />;
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

        return <Form onSubmit={onSubmit}>

            <FormGroup>
                <CustomInput
                    type="file" id="input-text-file"
                    label="Pick a text file to upload"
                    required onChange={onFileChange} />
            </FormGroup>

        </Form>;
    }

}
