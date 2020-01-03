import React from 'react';
import PropTypes from 'prop-types';
import { AppRedirect } from 'demo/approuter';
import gql from 'graphql-tag';
import { Mutation } from 'react-apollo';
import { Button } from 'reactstrap';


const MUTATION_DELETE_NOTE = gql`
    mutation deleteNote($id: Int!) {
        deleteNote(id: $id) {
            ok
        }
    }
`;


export default class DeleteNoteButton extends React.Component {
    static propTypes = {
        noteId: PropTypes.number.isRequired,
    };

    constructor(...args) {
        super(...args);
        this.state = {
            success: false,
        };
    }

    render() {
        if (this.state.success) {
            return <AppRedirect to="" />;
        }
        return <Mutation mutation={MUTATION_DELETE_NOTE}>
            {this._renderButton.bind(this)}
        </Mutation>;
    }

    _renderButton(deleteNote) {
        return <Button color="danger"
                       onClick={this._onClick.bind(this, deleteNote)}>
            Delete note
        </Button>;
    }

    _onClick(deleteNote) {
        const {noteId} = this.props;
        deleteNote({variables: {id: noteId}})
            .then(({data: {deleteNote: {ok}}}) => {
                if (ok) {
                    this.setState({success: true});
                }
            });
    }

}
