import { useMutation, useQuery } from '@tanstack/react-query';
import { message } from 'antd';
import api from 'api';
import { User, Organisation, AddUser, AddOrganisation } from 'api/models';

// Fetch organizations
export const useOrganizations = () => {
    return useQuery<Organisation[], Error>({
        queryKey: ['organisations'],
        queryFn: () => api.getOrganisations().then((res) => res.data),
    });
};

// Fetch users
export const useAllUsers = () => {
    return useQuery<User[], Error>({
        queryKey: ['users'],
        queryFn: () => api.getAllUsers().then((res) => res.data),
    });
};

// Create organization mutation
export const useCreateOrg = () => {
    const { refetch } = useOrganizations();
    return useMutation({
        mutationFn: (values: AddOrganisation) => api.insertOrganisation(values),
        onSuccess: () => {
            message.success('Organization created');
            refetch();
        },
        onError: () => message.error('Failed to create organization'),
    });
};

// Delete organization mutation
export const useDeleteOrg = () => {
    const { refetch } = useOrganizations();
    return useMutation({
        mutationFn: (orgId: string) => api.deleteOrganisation(orgId),
        onSuccess: () => {
            message.success('Organization deleted');
            refetch();
        },
        onError: () => message.error('Failed to delete organization'),
    });
};

// Create user mutation
export const useCreateUser = () => {
    const { refetch } = useAllUsers();
    const { refetch: refetchOrg } = useOrganizations();
    return useMutation({
        mutationFn: (values: AddUser) => api.createUser(values),
        onSuccess: () => {
            message.success('User created');
            refetch();
            refetchOrg();
        },
        onError: () => message.error('Failed to create user'),
    });
};

export const useDeleteUser = () => {
    const { refetch } = useAllUsers();
    const { refetch: refetchOrg } = useOrganizations();
    return useMutation({
        mutationFn: (userId: string) => api.deleteUser(userId),
        onSuccess: () => {
            message.success('User deleted');
            refetch();
            refetchOrg();
        },
        onError: () => message.error('Failed to delete user'),
    });
};