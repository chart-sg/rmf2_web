import { Snackbar, SnackbarProps } from '@material-ui/core';
import { Alert } from '@material-ui/lab';
import React from 'react';

export interface ErrorSnackbarProps extends SnackbarProps {
  message: string;
}

export function ErrorSnackbar({ message, ...otherProps }: ErrorSnackbarProps): JSX.Element {
  return (
    <Snackbar autoHideDuration={2000} {...otherProps}>
      <Alert severity="error">{message}</Alert>
    </Snackbar>
  );
}