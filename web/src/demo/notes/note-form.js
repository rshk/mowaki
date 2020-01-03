import React from 'react';
import PropTypes from 'prop-types';
import { AppLink } from 'demo/approuter';
import { Button, Form, FormGroup, Input } from 'reactstrap';


export  default function NoteForm({
    onSubmit, errorMessage, noteId, title, body,
    onTitleChange, onBodyChange, loading, error}) {

    const isTitleValid = !!title;
    const isBodyValid = !!body;

    const isFormValid = isTitleValid && isBodyValid;

    return <Form onSubmit={onSubmit}>

        {loading && <div>Loading...</div>}

        {/* Error returned in the GraphQL response */}
        {errorMessage && <div><strong>Error:</strong> {errorMessage}</div>}

        {/* Error raised by client, eg. connection error... */}
        {error && <div><strong>Error:</strong> {error.message}</div>}

        <FormGroup>
            <Input type="text" placeholder="Note title"
                   value={title} onChange={onTitleChange} />
        </FormGroup>

        <FormGroup>
            <Input type="textarea" rows="10"
                   value={body} onChange={onBodyChange} />
        </FormGroup>

        <div>
            <Button type="submit" disabled={!isFormValid}>
                {noteId ? 'Update note' : 'Create note'}
            </Button>{' '}
            {noteId && <AppLink to={`/note/${noteId}`}>Cancel</AppLink>}
        </div>

    </Form>;
}


NoteForm.propTypes = {
    onSubmit: PropTypes.func.isRequired,
    errorMessage: PropTypes.string,
    noteId: PropTypes.number,  // Update form only
    title: PropTypes.string.isRequired,
    body: PropTypes.string.isRequired,
    onTitleChange: PropTypes.func.isRequired,
    onBodyChange: PropTypes.func.isRequired,
};
