import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { createTicketFromEmail } from "@/api/tickets";
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
import type { TicketDetail } from "@/types/ticket";

const emailIntakeSchema = z.object({
  from_name: z.string().min(1, "Sender name is required").max(120),
  from_email: z.string().email("Enter a valid sender email"),
  email_subject: z.string().min(1, "Email subject is required").max(255),
  email_body: z.string().min(1, "Email body is required"),
});

type EmailIntakeFormValues = z.infer<typeof emailIntakeSchema>;

type EmailIntakeFormProps = {
  onTicketCreated: (ticket: TicketDetail) => void;
};

export function EmailIntakeForm({ onTicketCreated }: EmailIntakeFormProps) {
  const [submitError, setSubmitError] = useState<string | null>(null);

  const form = useForm<EmailIntakeFormValues>({
    resolver: zodResolver(emailIntakeSchema),
    defaultValues: {
      from_name: "",
      from_email: "",
      email_subject: "",
      email_body: "",
    },
  });

  async function onSubmit(values: EmailIntakeFormValues) {
    try {
      setSubmitError(null);

      const ticket = await createTicketFromEmail(values);

      form.reset({
        from_name: "",
        from_email: "",
        email_subject: "",
        email_body: "",
      });

      onTicketCreated(ticket);
    } catch (error) {
      console.error(error);
      setSubmitError(
        "Email-style ticket could not be created. Check that the backend is running."
      );
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Email-style intake</CardTitle>
        <CardDescription>
          Simulate a support email and convert it into a ticket. Real mailbox
          ingestion can be added later.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-5">
        {submitError ? (
          <div className="rounded-md border border-destructive bg-destructive/10 px-4 py-3 text-sm text-destructive">
            {submitError}
          </div>
        ) : null}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
            <div className="grid gap-5 md:grid-cols-2">
              <FormField
                control={form.control}
                name="from_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>From name</FormLabel>
                    <FormControl>
                      <Input placeholder="Adam Müller" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="from_email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>From email</FormLabel>
                    <FormControl>
                      <Input
                        type="email"
                        placeholder="adam@example.com"
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
              name="email_subject"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email subject</FormLabel>
                  <FormControl>
                    <Input placeholder="Invoice document attached" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="email_body"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email body</FormLabel>
                  <FormControl>
                    <Textarea
                      className="min-h-40"
                      placeholder="Hello support team, I attached my invoice document and need it processed..."
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit" disabled={form.formState.isSubmitting}>
              {form.formState.isSubmitting
                ? "Creating ticket..."
                : "Create Email Ticket"}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}