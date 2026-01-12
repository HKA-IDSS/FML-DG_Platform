import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../api';
import { AddGroup, Group } from '../api/models';
import { message } from 'antd';

// Fetch group by id
export function useGroup(groupId?: string, version?: number) {
    return useQuery<Group, Error>({
        queryKey: ['groups', groupId, version],
        queryFn: () => api.getGroupById(groupId!, version).then((res) => res.data),
        enabled: !!groupId,
    });
}

export function useGroups() {
    return useQuery<Group[], Error>({
        queryKey: ['groups'],
        queryFn: async () => {
            const res = await api.getGroups();
            return res.data;
        },
        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
    });
}

// Delete group mutation
export function useDeleteGroup() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (groupId: string) => api.deleteGroup(groupId),
        onSuccess: () => {
            message.success('Group deleted');
            queryClient.invalidateQueries({ queryKey: ['groups'] });
        },
        onError: () => {
            message.error('Failed to delete group');
        },
    });
}

// Add group mutation
export function useAddGroup() {
    const { refetch } = useGroups();
    return useMutation({
        mutationFn: (values: AddGroup) => api.insertGroup(values),
        onSuccess: () => {
            message.success('Group added');
            refetch();
        },
        onError: () => {
            message.error('Failed to save group');
        },
    });
}

export function useAddMember() {
    const { refetch } = useGroups();
    return useMutation({
        mutationFn: ({ groups, userId }: { groups: string[]; userId: string }) => {
            const promises = groups.map((group) => api.addMember(group, userId));
            return Promise.all(promises);
        },
        onSuccess: () => {
            message.success('User added to group');
            refetch();
        },
        onError: () => {
            message.error('Failed to add user to group');
        },
    });
}

// (Optional) Update group mutation
export function useUpdateGroup() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ groupId, values }: { groupId: string; values: AddGroup }) => api.updateGroup(groupId, values),

        onSuccess: () => {
            message.success('Group updated');
            queryClient.invalidateQueries({ queryKey: ['groups'] });
        },
        onError: () => {
            message.error('Failed to update group');
        },
    });
}
