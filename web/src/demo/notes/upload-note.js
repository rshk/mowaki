import React from 'react';
import gql from 'graphql-tag';
import { useMutation } from '@apollo/react-hooks';
import { Form, FormGroup, CustomInput } from 'reactstrap';
import { Alert } from 'reactstrap';

import { AppRedirect } from 'demo/approuter';


export default function UploadNoteForm() {

    const [uploadNote, mutationStatus] = useMutation(gql`
        mutation uploadNote($file: FileUpload!) {
            result: uploadNote(uploadedFile: $file) {
                ok
                noteId
                errorMessage
            }
        }
    `);

    const { error, data, called } = mutationStatus;

    if (error) {
        return <Alert color="danger">{error.message}</Alert>;
    }

    let errorMessage = null;

    if (called && data && data.result) {
        if (data.result.ok) {
            const { noteId } = data.result;
            return <AppRedirect to={`/note/${noteId}`} />;
        }
        errorMessage = data.result.errorMessage || 'Note upload failed';
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

    return <div>

        {!!errorMessage && <Alert color="danger">{errorMessage}</Alert>}

        <Form onSubmit={onSubmit}>

            <FormGroup>
                <CustomInput
                    type="file" id="input-text-file"
                    label="Pick a text file to upload"
                    required onChange={onFileChange} />
            </FormGroup>

        </Form>
    </div>;
}
