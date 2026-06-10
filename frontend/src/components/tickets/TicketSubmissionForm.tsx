import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { createTicket } from "@/api/tickets";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import type { Ticket, TicketSource } from "@/types/ticket";

const ticketFormSchema = z.object({
    requester_name: z.string().min(1, "Requester name is required").max(120),
    requester_email: z.string().email("Enter a valid email address"),
    subject: z.string().min(1, "Subject is required").max(255),
    description: z.string().min(1, "Description is required"),
    source: z.enum(["form", "email"]),
});

type TicketFormValues = z.infer<typeof ticketFormSchema>;

type TicketSubmissionFormProps = {
    onTicketCreated: (ticket: Ticket) => void;
};

export function TicketSubmissionForm({
    onTicketCreated,
}: TicketSubmissionFormProps) {
    const [submitError, setSubmitError] = useState<string | null>(null);
    const [createdTicket, setCreatedTicket] = useState<Ticket | null>(null);

    const form = useForm<TicketFormValues>({
        resolver: zodResolver(ticketFormSchema),
        defaultValues: {
            requester_name: "",
            requester_email: "",
            subject: "",
            description: "",
            source: "form",
        },
    });

    async function onSubmit(values: TicketFormValues) {
        try {
            setSubmitError(null);
            setCreatedTicket(null);

            const ticket = await createTicket({
                ...values,
                source: values.source as TicketSource,
            });

            setCreatedTicket(ticket);
            onTicketCreated(ticket);

            form.reset({
                requester_name: "",
                requester_email: "",
                subject: "",
                description: "",
                source: "form",
            });
        } catch (error) {
            console.error(error);
            setSubmitError(
                "Ticket could not be submitted. Check that the backend is running."
            );
        }
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>Submit a support request</CardTitle>
                <CardDescription>
                    Create a new ticket from a form.
                </CardDescription>
            </CardHeader>

            <CardContent className="space-y-5">
                {submitError ? (
                    <div className="rounded-md border border-destructive bg-destructive/10 px-4 py-3 text-sm text-destructive">
                        {submitError}
                    </div>
                ) : null}

                {createdTicket ? (
                    <div className="rounded-md border bg-muted px-4 py-3 text-sm">
                        Ticket created successfully:{" "}
                        <span className="font-medium">{createdTicket.subject}</span>
                    </div>
                ) : null}

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
                        <div className="grid gap-5 md:grid-cols-2">
                            <FormField
                                control={form.control}
                                name="requester_name"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Requester name</FormLabel>
                                        <FormControl>
                                            <Input placeholder="Maya Schneider" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="requester_email"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Requester email</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="email"
                                                placeholder="maya@example.com"
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>

                        <FormField
                            control={form.control}
                            name="subject"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Subject</FormLabel>
                                    <FormControl>
                                        <Input placeholder="I cannot log in" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="description"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Description</FormLabel>
                                    <FormControl>
                                        <Textarea
                                            placeholder="Describe the issue clearly..."
                                            className="min-h-32"
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="source"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Source</FormLabel>
                                    <FormControl>
                                        <select
                                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                            {...field}
                                        >
                                            <option value="form">Form</option>
                                            <option value="email">Email</option>
                                        </select>
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />


                        <Button type="submit" disabled={form.formState.isSubmitting}>
                            {form.formState.isSubmitting ? "Submitting..." : "Create Ticket"}
                        </Button>
                    </form>
                </Form>
            </CardContent>
        </Card>
    );
}