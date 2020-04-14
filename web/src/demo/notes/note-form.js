import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { AppLink } from 'demo/approuter';
import { Alert, Button, Form, FormGroup, Input } from 'reactstrap';


export default function NoteForm({
    formData,
    errorMessage,
    loading,
    onSubmit,
    noteId,
}) {

    const [formState, setFormState] = useState({
        title: '',
        text: '',
        ...formData,
    });

    const isFormValid = (
        true ||
        (validateTitle(formState.title) &&
        validateText(formState.text))
    );

    const _onSubmit = evt=> {
        evt.preventDefault();
        onSubmit(formState);
    };

    return <Form onSubmit={_onSubmit}>

        {loading && <div>Loading...</div>}

        {/* Error returned in the GraphQL response */}
        {errorMessage && <Alert color="danger">{errorMessage}</Alert>}

        <FormGroup>
            <Input type="text"
                   placeholder="Note title"
                   value={formState.title}
                   onChange={evt=> setFormState({...formState, title: evt.target.value})} />
        </FormGroup>

        <FormGroup>
            <Input type="textarea"
                   rows="10"
                   value={formState.text}
                   onChange={evt=> setFormState({...formState, text: evt.target.value})} />
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
    formData: PropTypes.object,
    errorMessage: PropTypes.string,
    loading: PropTypes.bool,
    onSubmit: PropTypes.func.isRequired,
    noteId: PropTypes.number,  // Update form only
};


const validateTitle = (title)=> !!title.trim();
const validateText = (text)=> true;  // Can be empty
